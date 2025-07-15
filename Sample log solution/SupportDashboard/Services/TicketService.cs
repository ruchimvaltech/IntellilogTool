namespace SupportDashboard.Services
{
    using SupportDashboard.Models;
    using System.Collections.Generic;
    using System.Linq;

    public class TicketService
    {
        private readonly List<Ticket> _tickets = new List<Ticket>();

        public TicketService()
        {
            Serilog.Log.Information("✅ TicketService singleton instance created");
        }

        public List<Ticket> GetAll()
        {
            return _tickets;
        }

        public void Add(Ticket ticket)
        {
            _tickets.Add(ticket);
        }

        public Ticket GetById(int id)
        {
            return _tickets.FirstOrDefault(t => t.Id == id);
        }
    }
}
